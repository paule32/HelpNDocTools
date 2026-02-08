# Generated from dBaseParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .dBaseParser import dBaseParser
else:
    from dBaseParser import dBaseParser

# This class defines a complete generic visitor for a parse tree produced by dBaseParser.

class dBaseParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by dBaseParser#input.
    def visitInput(self, ctx:dBaseParser.InputContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#item.
    def visitItem(self, ctx:dBaseParser.ItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#statement.
    def visitStatement(self, ctx:dBaseParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#createFileStmt.
    def visitCreateFileStmt(self, ctx:dBaseParser.CreateFileStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#handlerList.
    def visitHandlerList(self, ctx:dBaseParser.HandlerListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#breakStmt.
    def visitBreakStmt(self, ctx:dBaseParser.BreakStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#returnStmt.
    def visitReturnStmt(self, ctx:dBaseParser.ReturnStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#doStmt.
    def visitDoStmt(self, ctx:dBaseParser.DoStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#doTarget.
    def visitDoTarget(self, ctx:dBaseParser.DoTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#programRef.
    def visitProgramRef(self, ctx:dBaseParser.ProgramRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#parameterStmt.
    def visitParameterStmt(self, ctx:dBaseParser.ParameterStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#paramNames.
    def visitParamNames(self, ctx:dBaseParser.ParamNamesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#callExpr.
    def visitCallExpr(self, ctx:dBaseParser.CallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#doWhileStatement.
    def visitDoWhileStatement(self, ctx:dBaseParser.DoWhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#condition.
    def visitCondition(self, ctx:dBaseParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#logicalOr.
    def visitLogicalOr(self, ctx:dBaseParser.LogicalOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#logicalAnd.
    def visitLogicalAnd(self, ctx:dBaseParser.LogicalAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#logicalNot.
    def visitLogicalNot(self, ctx:dBaseParser.LogicalNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#comparison.
    def visitComparison(self, ctx:dBaseParser.ComparisonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#compareOp.
    def visitCompareOp(self, ctx:dBaseParser.CompareOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#localDeclStmt.
    def visitLocalDeclStmt(self, ctx:dBaseParser.LocalDeclStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#localAssignStmt.
    def visitLocalAssignStmt(self, ctx:dBaseParser.LocalAssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#deleteStmt.
    def visitDeleteStmt(self, ctx:dBaseParser.DeleteStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#forStmt.
    def visitForStmt(self, ctx:dBaseParser.ForStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#numberExpr.
    def visitNumberExpr(self, ctx:dBaseParser.NumberExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#assignStmt.
    def visitAssignStmt(self, ctx:dBaseParser.AssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#lvalue.
    def visitLvalue(self, ctx:dBaseParser.LvalueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#dottedRef.
    def visitDottedRef(self, ctx:dBaseParser.DottedRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#exprStmt.
    def visitExprStmt(self, ctx:dBaseParser.ExprStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#ifStmt.
    def visitIfStmt(self, ctx:dBaseParser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#block.
    def visitBlock(self, ctx:dBaseParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#writeStmt.
    def visitWriteStmt(self, ctx:dBaseParser.WriteStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#writeArg.
    def visitWriteArg(self, ctx:dBaseParser.WriteArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#classDecl.
    def visitClassDecl(self, ctx:dBaseParser.ClassDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#classBody.
    def visitClassBody(self, ctx:dBaseParser.ClassBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#classMember.
    def visitClassMember(self, ctx:dBaseParser.ClassMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#withStmt.
    def visitWithStmt(self, ctx:dBaseParser.WithStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#withTarget.
    def visitWithTarget(self, ctx:dBaseParser.WithTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#withBody.
    def visitWithBody(self, ctx:dBaseParser.WithBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#withAssignStmt.
    def visitWithAssignStmt(self, ctx:dBaseParser.WithAssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#withLvalue.
    def visitWithLvalue(self, ctx:dBaseParser.WithLvalueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#propertyDecl.
    def visitPropertyDecl(self, ctx:dBaseParser.PropertyDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#methodDecl.
    def visitMethodDecl(self, ctx:dBaseParser.MethodDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#paramList.
    def visitParamList(self, ctx:dBaseParser.ParamListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#callStmt.
    def visitCallStmt(self, ctx:dBaseParser.CallStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#callTarget.
    def visitCallTarget(self, ctx:dBaseParser.CallTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#qualifiedName.
    def visitQualifiedName(self, ctx:dBaseParser.QualifiedNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#argList.
    def visitArgList(self, ctx:dBaseParser.ArgListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#identifier.
    def visitIdentifier(self, ctx:dBaseParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#expr.
    def visitExpr(self, ctx:dBaseParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#additiveExpr.
    def visitAdditiveExpr(self, ctx:dBaseParser.AdditiveExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#multiplicativeExpr.
    def visitMultiplicativeExpr(self, ctx:dBaseParser.MultiplicativeExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#postfixExpr.
    def visitPostfixExpr(self, ctx:dBaseParser.PostfixExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#postfixSuffix.
    def visitPostfixSuffix(self, ctx:dBaseParser.PostfixSuffixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#newExpr.
    def visitNewExpr(self, ctx:dBaseParser.NewExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#memberExpr.
    def visitMemberExpr(self, ctx:dBaseParser.MemberExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#literal.
    def visitLiteral(self, ctx:dBaseParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dBaseParser#primary.
    def visitPrimary(self, ctx:dBaseParser.PrimaryContext):
        return self.visitChildren(ctx)



del dBaseParser